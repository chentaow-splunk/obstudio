FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim AS build
WORKDIR /src
COPY Checkout.Sample.csproj Program.cs ./
RUN dotnet publish -c Release -o /app --self-contained false -p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/runtime:8.0-bookworm-slim
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip ca-certificates && rm -rf /var/lib/apt/lists/*
RUN case "$TARGETARCH" in \
      arm64) arch=arm64; sha=5e029cdb4246c26064f15f9f009362d1f919604ea5a24f4dfe306b25ff24bd26 ;; \
      amd64) arch=x64; sha=3801716bbf0094c423c5c6b586e38b52f383aa1bc9c6bd4177bf4f3f6e32c384 ;; \
      *) echo 'Unsupported architecture' >&2; exit 1 ;; \
    esac \
    && curl -fsSL --retry 3 "https://github.com/signalfx/splunk-otel-dotnet/releases/download/v1.16.0/splunk-opentelemetry-dotnet-linux-glibc-${arch}.zip" -o /agent.zip \
    && echo "$sha  /agent.zip" | sha256sum -c - \
    && unzip -q /agent.zip -d /otel && rm /agent.zip \
    && ln -s "/otel/linux-${arch}/OpenTelemetry.AutoInstrumentation.Native.so" /otel/Native.so
ENV OTEL_DOTNET_AUTO_HOME=/otel \
    CORECLR_ENABLE_PROFILING=1 \
    CORECLR_PROFILER="{918728DD-259F-4A6A-AC2B-B85E1B658318}" \
    CORECLR_PROFILER_PATH=/otel/Native.so \
    DOTNET_STARTUP_HOOKS=/otel/net/OpenTelemetry.AutoInstrumentation.StartupHook.dll
WORKDIR /app
COPY --from=build /app/ ./
CMD ["dotnet", "Checkout.Sample.dll"]
