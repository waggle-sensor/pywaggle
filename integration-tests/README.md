# Integration Tests

This suite tests the behavior of pywaggle against RabbitMQ.

Before testing, we need to start RabbitMQ using:

```sh
docker-compose up -d
```

Now, you can run the test suite using:

```sh
./test
```

When you're done, you can stop RabbitMQ using:

```sh
docker-compose down
```
