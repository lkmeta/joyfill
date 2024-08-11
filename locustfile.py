from locust import HttpUser, TaskSet, task, between
import random

# Sample sentences with <blank> placeholders
test_sentences = [
    "Have a <blank> day.",
    "I can't believe how <blank> this project turned out!",
    "You should really try the <blank> pizza at that new place.",
    "My favorite hobby is <blank> on the weekends.",
    "This movie was <blank> than I expected.",
    "I love spending my afternoons <blank> at the park.",
    "The team did a <blank> job on the presentation.",
    "Her new dress looks absolutely <blank>.",
    "I would love to go <blank> this summer.",
    "The concert last night was <blank>.",
    "Learning new skills is always <blank>.",
    "He was feeling <blank> about the upcoming exam.",
    "The cake she baked was <blank>.",
    "This software is so <blank> to use!",
    "They had a <blank> time at the party.",
    "I can't wait to <blank> the new book.",
    "This has been a <blank> experience so far.",
    "The food at the restaurant was <blank>.",
    "We had a <blank> conversation about the project.",
    "The application was <blank>.",
]

class UserBehavior(TaskSet):
    @task(1)
    def index(self):
        # Test the root endpoint
        self.client.get("/")

    @task(2)
    def suggestions(self):
        # Pick a random sentence from the list
        sentence = random.choice(test_sentences)
        self.client.post("/suggestions", data={"text": sentence})

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Simulates a wait time between 1 and 5 seconds between tasks
