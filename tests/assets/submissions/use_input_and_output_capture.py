def check_output_and_stdout() -> int:
    a = input("the first number: ")
    b = input("the second number: ")
    int_product = int(float(a) * float(b))
    print(f"the product of {a} and {b} is {int_product}")
    return int_product
