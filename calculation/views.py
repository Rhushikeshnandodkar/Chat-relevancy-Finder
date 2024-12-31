from django.shortcuts import render
from .models import *
from django.shortcuts import render, get_object_or_404
from .models import Room
import os 
from .models import *
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from django.conf import settings
from sentence_transformers import SentenceTransformer, util
import torch
import pickle
# Create your views here.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models\\spam_detector_model.h5")
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, 'calculation', 'models', 'tokenizer.pickle')
rel_model = SentenceTransformer('all-MiniLM-L6-v2') 
model = load_model(MODEL_PATH)
with open(TOKENIZER_PATH, 'rb') as handle:
    tokenizer = pickle.load(handle)


def predict_spam(qestion):
    comment_seq = tokenizer.texts_to_sequences([qestion])
    comment_pad = pad_sequences(comment_seq, maxlen=100, padding='post')
    prediction = model.predict(comment_pad)[0][0]
    if prediction > 0.5:
        comment_tag = Comment.objects.create(comment=qestion, tag='Spam')
        comment_tag.save()
    else:
        comment_tag = Comment.objects.create(comment=qestion, tag='Not Spam')
        comment_tag.save()

def calculate_relevancy(content, questions):
    """
    Calculate relevancy scores for a list of questions against the given content.
    Args:
        content (str): The main content to compare questions against.
        questions (list): A list of non-spam questions.

    Returns:
        list: A list of tuples (question, score) sorted by relevancy score.
    """
    # Encode the content and questions
    content_embedding = rel_model.encode(content, convert_to_tensor=True)
    question_embeddings = rel_model.encode(questions, convert_to_tensor=True)

    # Calculate cosine similarity
    relevancy_scores = util.pytorch_cos_sim(content_embedding, question_embeddings)

    # Prepare results: Each question with its corresponding score
    scores = relevancy_scores.squeeze().tolist()
    print(scores)
    # results = [(questions[i], scores[i]) for i in range(len(questions))]
    results = [(questions[i], scores[i]) for i in range(len(questions))]
    print("Results:", results)
    # Sort results by relevancy score (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def index(request):
    machines = MachineModel.objects.all()
    if request.method == "POST":
        value = request.POST.get('radius')
        if value:
            predict_spam(value)
    return render(request, "index.html", {'machines' : machines})

def show_board(request):
    content = '''
    Objective Function
The objective of gradient descent is to minimize a function f(θ)f(θ), typically the loss function that measures how well the model predicts the output.

Gradient

    The gradient of a function is the vector of its partial derivatives with respect to all variables.
    It indicates the direction and rate of the steepest ascent. For minimization, we move in the opposite direction of the gradient.

Learning Rate (αα)

    A hyperparameter that determines the step size in each iteration.
    Small learning rates result in slow convergence, while large learning rates can lead to overshooting the minimum.

Convergence

    Gradient descent iteratively updates the parameters until the gradient is close to zero or the change in the loss function becomes negligible.
    '''
    not_spam = Comment.objects.filter(tag="Not Spam")
    not_spam_list = []
    for i in not_spam:
        not_spam_list.append(i.comment)
    print(not_spam)
    rel_results = calculate_relevancy(content, not_spam_list)
    print(calculate_relevancy)
    return render(request, "showboard.html", {'results': rel_results})


def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room, created = Room.objects.get_or_create(name=room_name)
        return render(request, 'chat/room.html', {'room_name': room.name})
    return render(request, 'chat/create_room.html')

def room_view(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    return render(request, 'room.html', {'room_name': room.name})