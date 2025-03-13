SEQ = [1, 2, 3, 45, 356, 569, 600, 705, 923]

def search(number: int, seq: list[int] = SEQ) -> bool:
    left = 0
    right = len(seq) - 1
    while left <= right:
        mid = (left + right) // 2
        if seq[mid] == number:
            return True
        elif seq[mid] < number:
            left = mid + 1
        else:
            right = mid - 1
    return False
