from inference import predict_next_exercise

student_state = {
    "skill_proficiency": {
        "1a": 1.0,
        "2a": 0.2,
        "2b": 0.0,
        "3a": 0.0
    }
}

result = predict_next_exercise(student_state)

print(result)