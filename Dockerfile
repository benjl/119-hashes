FROM rust:1.91 AS builder
RUN apt-get update && apt-get install -y git
WORKDIR /usr/src/
RUN git clone https://github.com/benjl/119-hashes.git && cd 119-hashes && git checkout rust

WORKDIR /usr/src/119-hashes/find_119_rust
RUN cargo build --release

FROM alpine:3
RUN apk add --no-cache bash gcompat libstdc++
COPY --from=builder /usr/src/119-hashes/find_119_rust/target/release/find_119_rust /usr/119rust/find_119_rust

COPY init.sh /init.sh
RUN chmod +x /init.sh

WORKDIR /usr/119rust
ENTRYPOINT ["/bin/bash", "/init.sh"]
CMD ["/usr/119rust/find_119_rust", "slow", "resume", "noinput"]