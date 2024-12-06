from sage.all import log

# Define parameters
q = 2^32
n = 1000
m = 1002
t = 2^16
w = 86
b = 1001

# Check conditions
def check_parameters(q, n, m, t, w, b):
    conditions = {
        "Condition 1: n + 1 < m < n^2": n + 1 < m < n^2,
        "Condition 2: n < b": n < b,
        "Condition 3: (2 * log2(b) * b + 2) * b < q": ((2 * log(b, 2) * b + 2) * b) < q,
        "Condition 4: 2 * log2(b) < n": (2 * log(b, 2)) < n
    }
    
    # Print results
    for description, result in conditions.items():
        print(f"{description}: {'Passed' if result else 'Failed'}")

# Run the check
check_parameters(q, n, m, t, w, b)
