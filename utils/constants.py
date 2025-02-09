from google.ai.generativelanguage_v1beta.types import content

generation_config = {
    "temperature": 1,
    "response_schema": content.Schema(
        type=content.Type.ARRAY,
        description="Extracted structured questions and options from the input image, with a flag indicating whether the question or any of its options contains a figure or diagram.",
        items=content.Schema(
            type=content.Type.OBJECT,
            properties={
                "question_text": content.Schema(
                    type=content.Type.STRING,
                    description="The extracted question text."
                ),
                "contains_figure_or_diagram": content.Schema(
                    type=content.Type.BOOLEAN,
                    description="Indicates if the question or any of its options contains a figure or diagram."
                ),
                "options": content.Schema(
                    type=content.Type.ARRAY,
                    description="List of answer options.",
                    items=content.Schema(
                        type=content.Type.OBJECT,
                        properties={
                            "text": content.Schema(
                                type=content.Type.STRING,
                                description="The text of the option (if applicable)."
                            )
                        },
                        required=["text"]
                    )
                ),
            },
            required=["question_text", "options", "contains_figure_or_diagram"]
        )
    ),
    "response_mime_type": "application/json",
}


prompt = """Extract structured question data from the input image. For each question, include:
            - The full question text.
            - A boolean flag indicating whether the question or any of its options contains a figure or diagram (e.g., images, graphs, or illustrations).
            - A list of answer options, where each option is represented by its text.
            
            Please ensure that the response is structured according to the provided schema and includes all necessary details, such as the question text, any figures/diagrams, and all answer options.
        """
