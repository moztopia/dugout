ARG FLUTTER_VERSION=3.44.2
ARG FLUTTER_ARCHIVE_SHA256=b0de1d19754688ec6769c9a067db3b0594479d3d767f971bfecfc132904c8d5e
ARG ANDROID_COMMAND_LINE_TOOLS_VERSION=15859902
ARG ANDROID_COMMAND_LINE_TOOLS_SHA256=4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583
ARG ANDROID_PLATFORM_VERSION=36
ARG ANDROID_BUILD_TOOLS_VERSION=36.0.0

FROM debian:bookworm-slim AS flutter

ARG FLUTTER_VERSION
ARG FLUTTER_ARCHIVE_SHA256
ARG ANDROID_COMMAND_LINE_TOOLS_VERSION
ARG ANDROID_COMMAND_LINE_TOOLS_SHA256
ARG ANDROID_PLATFORM_VERSION
ARG ANDROID_BUILD_TOOLS_VERSION

LABEL org.opencontainers.image.title="Dugout Flutter tool"
LABEL org.opencontainers.image.description="Flutter SDK with command-line Android build tooling"
LABEL org.opencontainers.image.source="https://github.com/mozrin/dugout"
LABEL dev.moztopia.dugout.flutter.version="${FLUTTER_VERSION}"
LABEL dev.moztopia.dugout.android.platform="${ANDROID_PLATFORM_VERSION}"

ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV FLUTTER_ROOT=/opt/flutter
ENV PATH=/opt/flutter/bin:/opt/flutter/bin/cache/dart-sdk/bin:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:${PATH}
ENV CI=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        libglu1-mesa \
        openjdk-17-jdk-headless \
        unzip \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl --fail --location --show-error \
        --output /tmp/android-command-line-tools.zip \
        "https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_COMMAND_LINE_TOOLS_VERSION}_latest.zip" \
    && printf '%s  %s\n' \
        "${ANDROID_COMMAND_LINE_TOOLS_SHA256}" \
        /tmp/android-command-line-tools.zip \
        | sha256sum --check --strict \
    && mkdir -p "${ANDROID_HOME}/cmdline-tools/latest" \
    && unzip -q /tmp/android-command-line-tools.zip -d /tmp/android-command-line-tools \
    && mv /tmp/android-command-line-tools/cmdline-tools/* \
        "${ANDROID_HOME}/cmdline-tools/latest/" \
    && rm -rf \
        /tmp/android-command-line-tools \
        /tmp/android-command-line-tools.zip \
    && yes | sdkmanager --licenses >/dev/null \
    && sdkmanager \
        "build-tools;${ANDROID_BUILD_TOOLS_VERSION}" \
        "platform-tools" \
        "platforms;android-${ANDROID_PLATFORM_VERSION}"

RUN curl --fail --location --show-error \
        --output /tmp/flutter.tar.xz \
        "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz" \
    && printf '%s  %s\n' \
        "${FLUTTER_ARCHIVE_SHA256}" \
        /tmp/flutter.tar.xz \
        | sha256sum --check --strict \
    && tar -xJf /tmp/flutter.tar.xz -C /opt \
    && rm /tmp/flutter.tar.xz \
    && git config --system --add safe.directory /opt/flutter \
    && flutter config --no-analytics \
    && dart --disable-analytics \
    && flutter precache --android --web

RUN flutter precache

ARG ANDROID_NDK_VERSION=28.2.13676358
LABEL dev.moztopia.dugout.android.ndk="${ANDROID_NDK_VERSION}"

RUN sdkmanager "ndk;${ANDROID_NDK_VERSION}"

COPY tools/flutter/flutter-entrypoint /usr/local/bin/flutter-entrypoint

RUN chmod 0755 /usr/local/bin/flutter-entrypoint \
    && chmod -R a+rwX /opt/flutter \
    && chmod -R a+rwX /opt/android-sdk

ARG ANDROID_CMAKE_VERSION=3.22.1
LABEL dev.moztopia.dugout.android.cmake="${ANDROID_CMAKE_VERSION}"

RUN sdkmanager "cmake;${ANDROID_CMAKE_VERSION}" \
    && find /opt/android-sdk \
        -mindepth 1 \
        -maxdepth 1 \
        -type d \
        -exec chmod a+rwx {} + \
    && find /opt/android-sdk \
        -maxdepth 1 \
        -type f \
        -exec chmod a+rw {} +

COPY tools/flutter/update-engine-version /opt/flutter/bin/internal/update_engine_version.sh

RUN chmod 0755 /opt/flutter/bin/internal/update_engine_version.sh

WORKDIR /workspace

ENTRYPOINT ["flutter-entrypoint"]
CMD ["--help"]
