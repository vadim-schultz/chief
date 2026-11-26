---
name: pydantic
description: Working rules for Pydantic v2: model validation, partial writes with exclude_none, pydantic-settings for environment settings and discriminated unions. Use when a request names Pydantic, a model, a schema, settings or a validation error.
---

# Pydantic

Pydantic validates data into typed models. Use the v2 API. For the current version and new features, follow the docs-lookup skill in the stack-docs pack.

## Agent tooling

- MCP: none verified
- Endpoint: none
- Auth: none. The library has no hosted server.
- Scope: read-only first. Read the models before you change a validator.
- Docs index: https://pydantic.dev/docs/validation/latest/integrations/llms/
- Verified: 2026-11-26 https://pydantic.dev/docs/validation/latest/integrations/llms/
- Verified: 2026-11-26 https://pydantic.dev/docs/validation/latest/llms.txt
- Verified: 2026-11-26 https://pydantic.dev/docs/validation/latest/concepts/models/
- Verified: 2026-11-26 https://pydantic.dev/docs/validation/latest/concepts/serialization/
- Verified: 2026-11-26 https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
- Verified: 2026-11-26 https://pydantic.dev/docs/validation/latest/concepts/unions/

## When the server is missing

The vendor publishes an LLM documentation index, but no MCP server. Its index page says that LLM frameworks and IDEs cannot use these files natively, and it suggests an MCP server as a workaround. This skill names no MCP server. Read the index with the docs-lookup skill.

If the project adds an MCP server for these files, follow the mcp-setup skill. The agent never edits MCP configuration.

## Working rules

- Use the v2 API. `Model.model_validate(data)` validates a dictionary into a model, and `model.model_dump()` returns a dictionary. See https://pydantic.dev/docs/validation/latest/concepts/models/
- For a partial write, call `model.model_dump(exclude_none=True)`. It excludes each field whose value is None, so optional fields that are unset stay out of the write. See https://pydantic.dev/docs/validation/latest/concepts/serialization/
- Load environment settings with `pydantic-settings`, which is a separate package. A `BaseSettings` subclass looks up each field that you do not pass as a keyword argument in the environment. See https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
- Use a discriminated union when a value is one of several models. Give each model a shared field typed with a `Literal` value, and validate the union with `TypeAdapter`. See https://pydantic.dev/docs/validation/latest/concepts/unions/
- Check the current version and API on the vendor pages before you state them.
