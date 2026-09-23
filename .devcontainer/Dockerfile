FROM espressif/idf:v5.5.2

ARG DEBIAN_FRONTEND=nointeractive
ARG CONTAINER_USER=esp
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN apt-get update \
  && apt install -y -q \
  cmake \
  curl \
  git \
  hwdata \
  libglib2.0-0 \
  libnuma1 \
  libpixman-1-0 \
  linux-tools-virtual \
  && rm -rf /var/lib/apt/lists/*

# Node.js (required by the Claude Code CLI) + Claude Code itself
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y -q nodejs \
  && rm -rf /var/lib/apt/lists/* \
  && npm install -g @anthropic-ai/claude-code

# KiCad 9 (kicad-cli) - required to run ERC, DRC, netlist and BOM exports
# headlessly against pcb/BasisStation/*. The schematic files use format version
# 20250114, so KiCad 9 is mandatory; noble only ships KiCad 8, hence the PPA.
# Symbols and footprints are needed to resolve the project libraries; the
# metapackage kicad-libraries is avoided because it drags in kicad-packages3d
# (3.2 GB), which only matters for STEP/VRML exports. Add that package here if
# 3D output ever becomes relevant. xvfb covers the export subcommands that
# still expect an X display.
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends \
  software-properties-common \
  && DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:kicad/kicad-9.0-releases \
  && DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends \
  kicad \
  kicad-symbols \
  kicad-footprints \
  xvfb \
  && rm -rf /var/lib/apt/lists/*

# LibreOffice Calc (headless) - needed to recalculate generated .xlsx workbooks.
# openpyxl writes formulas as plain strings without cached results, so anything
# reading cached values (pandas, openpyxl data_only=True, previewers) sees empty
# cells until a real spreadsheet engine has evaluated them. soffice also surfaces
# formula errors that would otherwise ship unnoticed. Only the Calc component is
# installed; the full metapackage drags in Writer, Impress and Java.
# fonts-liberation provides metric-compatible substitutes for Arial, so column
# widths in generated workbooks render as intended.
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends \
  libreoffice-calc \
  libreoffice-core \
  fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/local/bin/usbip usbip `ls /usr/lib/linux-tools/*/usbip | tail -n1` 20

# QEMU
ENV QEMU_REL=esp-develop-20220919
ENV QEMU_SHA256=f6565d3f0d1e463a63a7f81aec94cce62df662bd42fc7606de4b4418ed55f870
ENV QEMU_DIST=qemu-${QEMU_REL}.tar.bz2
ENV QEMU_URL=https://github.com/espressif/qemu/releases/download/${QEMU_REL}/${QEMU_DIST}

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN wget --no-verbose ${QEMU_URL} \
  && echo "${QEMU_SHA256} *${QEMU_DIST}" | sha256sum --check --strict - \
  && tar -xf $QEMU_DIST -C /opt \
  && rm ${QEMU_DIST}

ENV PATH=/opt/qemu/bin:${PATH}

RUN groupadd --gid $USER_GID $CONTAINER_USER \
  && adduser --uid $USER_UID --gid $USER_GID --disabled-password --gecos "" ${CONTAINER_USER} \
  && usermod -a -G root $CONTAINER_USER && usermod -a -G dialout $CONTAINER_USER

# Stable alias for the IDF Python virtualenv - its directory name carries the IDF and
# Python versions, so pin-bumps would otherwise break idf.pythonBinPath in devcontainer.json
RUN set -eux; \
  env_dir="$(find /opt/esp/python_env -mindepth 1 -maxdepth 1 -type d -name 'idf*_env' | head -n1)"; \
  test -n "$env_dir"; \
  ln -sfn "$env_dir" /opt/esp/python_env/current

# Spreadsheet tooling for the BOM exports (SHBS-14). Installed into the IDF
# virtualenv because that is the python3 on PATH; the "current" symlink above
# keeps this independent of the IDF/Python version in the directory name.
RUN /opt/esp/python_env/current/bin/pip install --no-cache-dir \
  openpyxl \
  pandas

RUN chmod -R 775 /opt/esp/python_env/

USER ${CONTAINER_USER}
ENV USER=${CONTAINER_USER}
WORKDIR /home/${CONTAINER_USER}

RUN echo "source /opt/esp/idf/export.sh > /dev/null 2>&1" >> ~/.bashrc

# Claude Codes Zustandsverzeichnis anlegen, solange noch das Image gebaut wird.
# devcontainer.json mountet ein Named Volume darauf; Docker uebernimmt Inhalt und
# Eigentuemer eines leeren Volumes aus dem Image. Fehlt das Verzeichnis hier,
# legt Docker es als root:root an und der Container-User kann nicht hineinschreiben.
RUN mkdir -p ~/.claude

# Seed KiCad's global library tables for the container user. kicad-cli creates
# fp-lib-table by itself on first run, but not sym-lib-table - without it every
# stock library (power, Device, Connector, ...) is reported missing and ERC
# drowns in lib_symbol_issues violations.
RUN mkdir -p ~/.config/kicad/9.0 \
  && cp /usr/share/kicad/template/sym-lib-table ~/.config/kicad/9.0/sym-lib-table \
  && cp /usr/share/kicad/template/fp-lib-table ~/.config/kicad/9.0/fp-lib-table

ENTRYPOINT [ "/opt/esp/entrypoint.sh" ]

CMD ["/bin/bash", "-c"]