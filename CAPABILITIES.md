# GPT Image capability mapping

Compared with [MCPs at f0eed10abf31](https://github.com/AceDataCloud/MCPs/tree/f0eed10abf310824cb4c33d4944c63d3654ac95b/openai) and the public API contract at PlatformBackend `fa94598267a82545fb1afed6ee26bafd6cbb9ca7`.

This image plugin covers OpenAI image generation, editing and image-task APIs. Chat Completions are provided by ModelProviderDify. Responses, embeddings, speech and Realtime are outside this image plugin; they are not claimed as covered.

| MCP function | Dify equivalent | Notes |
|---|---|---|
| `openai_chat_completion` |  | Outside this image plugin: see scope above. |
| `openai_create_response` |  | Outside this image plugin: see scope above. |
| `openai_get_models` |  | Outside this image plugin: see scope above. |
| `openai_get_realtime_connection_info` |  | Outside this image plugin: see scope above. |
| `openai_list_chat_models` |  | Outside this image plugin: see scope above. |
| `openai_list_image_models` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `openai_list_embedding_models` |  | Outside this image plugin: see scope above. |
| `openai_get_usage_guide` |  | Outside this image plugin: see scope above. |
| `openai_text_to_speech` |  | Outside this image plugin: see scope above. |
| `openai_transcribe_audio` |  | Outside this image plugin: see scope above. |
| `openai_get_task` | `gpt_image_task_retrieve` | Set action=retrieve |
| `openai_list_tasks` | `gpt_image_list_tasks` | Set action=retrieve_batch |
| `openai_generate_image` | `gpt_image_generate_image` |  |
| `openai_edit_image` | `gpt_image_edit_image` |  |
| `openai_create_embedding` |  | Outside this image plugin: see scope above. |

## Parameter equivalents

- `openai_chat_completion`: `n` → count, `stream` → Dify submit/poll output: async=true, stream=false, `response_format` → URL output for Dify media.
- `openai_create_response`: `n` → count, `response_format` → URL output for Dify media, `stream` → Dify submit/poll output: async=true, stream=false.
- `openai_text_to_speech`: `response_format` → URL output for Dify media.
- `openai_transcribe_audio`: `response_format` → URL output for Dify media, `stream` → Dify submit/poll output: async=true, stream=false.
- `openai_get_task`: `id` → task_id.
- `openai_generate_image`: `n` → count, `response_format` → URL output for Dify media, `async_` → Dify submit/poll output: async=true, stream=false.
- `openai_edit_image`: `image` → image_urls, `n` → count, `response_format` → URL output for Dify media, `async_` → Dify submit/poll output: async=true, stream=false.

## Verification boundary

Contract examples and regression tests cover request validation, transport and task handling. Actual Dify browser cases are recorded separately in `tests/e2e-results.json` and `tests/e2e-audit.json` when available. A schema test is not a successful paid generation. Unsupported service availability and untested advanced combinations must not be described as passed.
