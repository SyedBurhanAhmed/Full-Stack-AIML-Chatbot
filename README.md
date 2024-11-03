# AIML Chatbot 🚀

Welcome to the AIML Chatbot project! This is a full-stack chatbot built using Python, the `python-aiml` library, and the Flask framework. Initially inspired by Pema Gurung's AIML chatbot and kuki.ai (a multiple Loebner Prize winner), this chatbot explores the capabilities of rule-based chatbots. Unlike AI-driven bots that evolve through machine learning or NLP, this chatbot is entirely scripted, making it ideal for specific use cases.

## Features 🌟

- **Rule-Based Responses**: Predefined responses for every potential input, making it perfect for domain-specific applications.
- **NLP Integration**: Added NLP capabilities using WordNet to answer "what" and "who" questions.
- **Sentiment Analysis**: The chatbot analyzes the user's mood; if it detects a negative sentiment, it responds with a joke.
- **Customizable**: Implemented on the web using the Flask framework, with customizable HTML based on Pema Gurung's project.
- **Speech Recognition**: Allows users to interact with the chatbot using voice commands.
- **Text-to-Speech**: Converts chatbot responses into spoken words for an enhanced user experience.
- **User Authentication**: Supports login and signup functionality for personalized interactions.
- **Chat History Management**: Saves and retrieves past interactions, allowing users to revisit previous conversations.
- **Neo4j Integration**: Utilizes Neo4j as a graph database for managing user preferences and relationships.
- **Dynamic Responses**: Generates contextually relevant responses based on user queries and history.
- **Future Enhancements**: Plans to implement backend functionalities for login and signup pages and integrate a graph database (Neo4j) for more complex interactions.

## Use Cases 🎯

1. **Customer Support**: Handles frequently asked questions (FAQs) with ease.
2. **Domain-Specific Bots**: Ideal for industries that require specialized knowledge.
3. **Appointment Booking**: Streamlines scheduling tasks, making it easier to manage bookings.

## Installation 🛠️

To run this project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/aiml-chatbot.git
   ```
   
2. **Navigate to the project directory**:
   ```bash
   cd aiml-chatbot
   ```

3. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

4. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Flask application**:
   ```bash
   flask run
   ```
   The application will be available at `http://127.0.0.1:5000/`.

## Usage 🚀

Once the application is running, you can interact with the chatbot through the web interface. The bot can:

- Answer predefined questions.
- Respond to "what" and "who" questions using WordNet.
- Tell a joke if it detects a negative sentiment from the user.
- Engage users through voice interactions and deliver responses audibly.

## Future Plans 🔮

- **General-Purpose Bot**: Enhance the chatbot to handle more general queries and tasks.
- **Graph Database Integration**: Implement Neo4j to manage complex relationships between data points.
- **Backend Implementation**: Add login and signup functionality to manage user sessions and data.

## Contributions 🤝

Contributions are welcome! If you have ideas for improvements or new features, feel free to fork the repository and submit a pull request.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments 🙏

- Inspired by [Pema Gurung's AIML chatbot](https://github.com/pemagurung/AIML-Chatbot).
- Thanks to kuki.ai for being a benchmark in rule-based chatbots.
