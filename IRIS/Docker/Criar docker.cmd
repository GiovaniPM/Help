docker run \
    -d \
    --name my-iris \
    -p 1972:1972 \
    -p 52773:52773 \
    -v iris_data:/durable \
    intersystems/iris-community:latest-em