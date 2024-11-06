FROM golang:alpine AS build
WORKDIR /app
COPY . .
RUN go build -o main

FROM alpine
WORKDIR /app
COPY --from=build /app/main /app/main
CMD ["/app/main"]
