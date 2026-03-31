def calculate_average_rating(reviews):
    sum = 0
    count = 0
    for review in reviews:
        sum += review.rating
        count += 1
    if count == 0:
        return -1
    return round(sum/count, 2)
