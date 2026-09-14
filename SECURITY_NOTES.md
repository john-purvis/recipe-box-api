# Security baseline

- 2026-09-14 – Anonymous `GET /recipes` → 200 OK, returns all recipes including `is_public: false`.
- 2026-09-14 – Anonymous `POST /recipes` → 201 CREATED, new recipe persisted.
- 2026-09-14 – Anonymous `PATCH /recipes/4` → 200 OK, recipe 4 updated.
- 2026-09-14 – Anonymous `DELETE /recipes/4` → 204 NO CONTENT, recipe 4 deleted.
