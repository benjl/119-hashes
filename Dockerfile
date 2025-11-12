FROM rust:1.91 AS builder

COPY ./find_119_rust /usr/src/find_119_rust

WORKDIR /usr/src/find_119_rust
RUN cargo build --release

FROM alpine:3
RUN apk add --no-cache bash gcompat libstdc++
COPY --from=builder /usr/src/find_119_rust/target/release/find_119_rust /usr/119rust/find_119_rust

WORKDIR /usr/119rust/
CMD ["/usr/119rust/find_119_rust", "resume"]