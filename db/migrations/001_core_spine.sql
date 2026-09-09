-- WP1 · Migration 001 — Core platform spine
-- The five-object model from the WP1 Architecture Dossier §2:
-- Organization → Property → User/Role, Guest/Stay, Task, Message, Content.
-- Generic by design: carries the ISS marketing/intelligence case now and
-- the guest & ops use cases later without schema changes.

create extension if not exists pgcrypto;

-- ── Tenancy ────────────────────────────────────────────────────────────────

create table organizations (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  kind        text not null default 'group' check (kind in ('group','independent')),
  created_at  timestamptz not null default now()
);

create table properties (
  id          uuid primary key default gen_random_uuid(),
  org_id      uuid not null references organizations(id),
  name        text not null,
  region      text,
  -- per-property branding resolved at request time (dossier §3)
  branding    jsonb not null default '{}',
  created_at  timestamptz not null default now()
);

create table departments (
  id          uuid primary key default gen_random_uuid(),
  property_id uuid not null references properties(id),
  name        text not null,
  unique (property_id, name)
);

-- ── Users & roles (dossier §4) ─────────────────────────────────────────────

create table users (
  id          uuid primary key default gen_random_uuid(),
  email       text not null unique,
  full_name   text not null,
  created_at  timestamptz not null default now()
);

create table memberships (
  user_id     uuid not null references users(id),
  org_id      uuid not null references organizations(id),
  property_id uuid references properties(id),      -- null = org-wide role
  department_id uuid references departments(id),   -- null = property-wide
  role        text not null check (role in
    ('platform_admin','org_admin','property_manager','staff')),
  primary key (user_id, org_id, role)
);

-- ── Guests & stays (future guest&ops use case; unused by ISS PoC) ──────────

create table guests (
  id          uuid primary key default gen_random_uuid(),
  full_name   text,
  channel_handle text,          -- e.g. WhatsApp number; minimized per GDPR
  created_at  timestamptz not null default now()
);

create table stays (
  id            uuid primary key default gen_random_uuid(),
  property_id   uuid not null references properties(id),
  guest_id      uuid not null references guests(id),
  external_ref  text,           -- PMS reservation id (e.g. Mews ReservationId)
  room          text,
  starts_on     date not null,
  ends_on       date not null
);

-- ── Tasks: the unit of operational work, with provenance ──────────────────

create table tasks (
  id            uuid primary key default gen_random_uuid(),
  property_id   uuid not null references properties(id),
  department_id uuid references departments(id),
  title         text not null,
  detail        text,
  status        text not null default 'open' check (status in ('open','in_progress','done','cancelled')),
  -- provenance: what created this task (dossier §2 — this chain IS the demo)
  origin_kind   text not null check (origin_kind in ('message','match','advice','manual','pms_event')),
  origin_id     uuid,
  assigned_to   uuid references users(id),
  created_at    timestamptz not null default now(),
  closed_at     timestamptz
);

-- ── Messages: channel-agnostic threads ─────────────────────────────────────

create table threads (
  id          uuid primary key default gen_random_uuid(),
  property_id uuid not null references properties(id),
  stay_id     uuid references stays(id),
  channel     text not null default 'web' check (channel in ('web','whatsapp','pms','email','internal')),
  created_at  timestamptz not null default now()
);

create table messages (
  id          uuid primary key default gen_random_uuid(),
  thread_id   uuid not null references threads(id),
  sender_kind text not null check (sender_kind in ('guest','staff','system','ai')),
  sender_id   uuid,
  body        text not null,
  language    text,
  created_at  timestamptz not null default now()
);

-- ── Content: versioned, layered org→property (dossier §2) ──────────────────

create table content (
  id          uuid primary key default gen_random_uuid(),
  org_id      uuid not null references organizations(id),
  property_id uuid references properties(id),  -- null = org-level default
  kind        text not null,                   -- 'compendium','brand_rule','house_info',...
  title       text not null,
  body        jsonb not null,
  version     int  not null default 1,
  updated_at  timestamptz not null default now()
);

create index on properties (org_id);
create index on tasks (property_id, status);
create index on messages (thread_id, created_at);
create index on content (org_id, property_id, kind);
