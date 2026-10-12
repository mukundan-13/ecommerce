
import grpc

import product_pb2
import product_pb2_grpc


def test_product(product_id: int):
    with grpc.insecure_channel("localhost:50052") as channel:
        client = product_pb2_grpc.ProductServiceStub(channel)

        request = product_pb2.GetProductRequest(
            product_id=product_id
        )

        try:
            response = client.GetProduct(request, timeout=5)

            print("\nProduct found!")
            print("ID:", response.id)
            print("Name:", response.name)
            print("Price:", response.price)
            print("Active:", response.is_active)

        except grpc.RpcError as error:
            print("\n gRPC error:", error.code())
            print("Details:", error.details())


if __name__ == "__main__":
    test_product(1)
    test_product(20)
