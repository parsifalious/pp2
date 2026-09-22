def filter_prime(nums):
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0:
                return False
        return True
    return [n for n in nums if is_prime(n)]

print(filter_prime([1,2,3,4,5,6,7,8,9,10]))