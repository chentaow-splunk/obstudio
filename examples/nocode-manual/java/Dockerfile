FROM eclipse-temurin:21-jdk-jammy
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL --retry 3 https://github.com/signalfx/splunk-otel-java/releases/download/v2.33.1/splunk-otel-javaagent.jar -o /agent.jar \
    && echo '8f98c8b4cce44b22451d825be7e894c8897d9f3fada526b937aab183bf0e7972  /agent.jar' | sha256sum -c -
WORKDIR /app
COPY CheckoutService.java ./
RUN javac -d /app CheckoutService.java
CMD ["java", "-javaagent:/agent.jar", "-cp", "/app", "lab.CheckoutService"]
