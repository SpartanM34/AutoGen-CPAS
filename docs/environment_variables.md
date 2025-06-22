# Environment Variables

This repository uses several environment variables for the Python and .NET samples. Set these variables in your shell or configure them in an `ENV.yaml` file.

## Common Keys

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI key used by most Python and .NET examples. |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key used with `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOY_NAME`. |
| `AZURE_OPENAI_ENDPOINT` | Endpoint URL for Azure OpenAI. |
| `AZURE_OPENAI_DEPLOY_NAME` | Deployment name for Azure OpenAI. |
| `AZURE_OPENAI_AD_TOKEN` | Azure Active Directory token when using AD authentication. |
| `BING_API_KEY` | Bing Search API key required by some samples. |
| `GOOGLE_GEMINI_API_KEY` | Google Gemini API key used in .NET samples. |
| `GCP_VERTEX_PROJECT_ID` | Google Cloud project ID for Vertex AI samples. |
| `ANTHROPIC_API_KEY` | Anthropic key for Claude-related samples. |

Other samples may use additional keys. Refer to the README for each sample for complete details.

## Example `ENV.yaml`

```yaml
OPENAI_API_KEY: <your-openai-api-key>
AZURE_OPENAI_API_KEY: <your-azure-openai-key>
AZURE_OPENAI_ENDPOINT: https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOY_NAME: <deployment-name>
AZURE_OPENAI_AD_TOKEN: <your-ad-token>
BING_API_KEY: <your-bing-api-key>
GOOGLE_GEMINI_API_KEY: <your-gemini-api-key>
GCP_VERTEX_PROJECT_ID: <your-project-id>
ANTHROPIC_API_KEY: <your-anthropic-api-key>
```

Save this file as `ENV.yaml` in the working directory of a sample if you prefer providing keys in a file rather than environment variables. The `agbench` benchmarks and other scripts will read these values when present.
