-- Store 3729 Inventory (Supabase) - schema v1
create extension if not exists "uuid-ossp";

-- Store settings (editable anytime)
create table if not exists app_settings (
  id uuid primary key default uuid_generate_v4(),
  store_number text not null,
  store_label text not null,
  intersection text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Units (editable anytime)
create table if not exists units (
  id uuid primary key default uuid_generate_v4(),
  name text not null unique,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

-- Locations (editable anytime)
create table if not exists locations (
  id uuid primary key default uuid_generate_v4(),
  name text not null unique,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

-- Items master list
create table if not exists items (
  id uuid primary key default uuid_generate_v4(),
  name text not null unique,
  base_unit_id uuid not null references units(id),
  case_size numeric(12,4),            -- 1 case = X base units (optional)
  allow_partials boolean not null default true,
  par_level numeric(12,4),
  low_threshold numeric(12,4),
  default_location_id uuid references locations(id),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Transfers (borrow/lend)
do $$ begin
  create type transfer_direction as enum ('BORROW_IN', 'LEND_OUT');
exception when duplicate_object then null; end $$;

do $$ begin
  create type transfer_status as enum ('REQUESTED','APPROVED','PICKED_UP','RETURNED','CLOSED');
exception when duplicate_object then null; end $$;

create table if not exists transfer_tickets (
  id uuid primary key default uuid_generate_v4(),
  direction transfer_direction not null,
  other_store text not null,
  status transfer_status not null default 'REQUESTED',
  notes text,
  photo_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists transfer_lines (
  id uuid primary key default uuid_generate_v4(),
  ticket_id uuid not null references transfer_tickets(id) on delete cascade,
  item_id uuid not null references items(id),
  qty_base_units numeric(12,4) not null
);

-- Inventory event log (history + totals)
do $$ begin
  create type event_type as enum (
    'COUNT_SET',
    'TRUCK_ADD',
    'WASTE_SUB',
    'TRANSFER_OUT_SUB',
    'TRANSFER_IN_ADD',
    'ADJUSTMENT'
  );
exception when duplicate_object then null; end $$;

create table if not exists inventory_events (
  id uuid primary key default uuid_generate_v4(),
  event_type event_type not null,
  item_id uuid not null references items(id),
  delta_base_units numeric(12,4) not null,
  notes text,
  photo_url text,
  ref_type text,
  ref_id uuid,
  client_event_id uuid not null unique,   -- offline dedupe
  device_id text not null,
  created_at timestamptz not null default now()
);

-- Shared login storage (hashed password)
create table if not exists auth_secrets (
  id int primary key default 1,
  username text not null,
  password_hash text not null,
  updated_at timestamptz not null default now()
);

-- Seed your store + defaults (editable later)
insert into app_settings (store_number, store_label, intersection)
values ('3729', 'Sonic Drive-In #3729', 'Gilbert & Baseline')
on conflict do nothing;

insert into units (name) values ('bag'), ('box'), ('sleeve'), ('unit')
on conflict do nothing;

insert into locations (name) values ('Freezer'), ('Small Fridge'), ('Dry Storage'), ('Back Room/Office'), ('Line')
on conflict do nothing;
