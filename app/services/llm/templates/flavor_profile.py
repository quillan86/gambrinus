from langchain import PromptTemplate

_template = """You are an expert taste tester of beer. The following is the perceived flavor of the beer that you taste.
The unnormalized flavor profile describes the individual intensity of flavors, from 0 to 100.
This measures how activated your taste buds or nose are to this particular flavor. 0 means no activation, 100 means completely activated; this is based off of the biochemical Hill Equation.
Flavor is composed of taste, odor, and texture.

The normalized flavor profile describes how competitive the flavors are - a percentage proportion of each flavor.

There might be other flavors, but these are the perceived tastes that we have recorded scientifically.
---
Answer the question by describing the flavor of the beer from this flavor profile as if you were tasting it.
Use both unnormalized and normalized parts of the flavor profile when describing the flavor.
Use detailed descriptive wording.
Try not to use the quantitative values in the description, but use them to create the detailed wording.
Feel free to infer additional parts of the flavor in the description.

Question:
```
{question}
```

Context:
```
{context}
```

Description:"""
FLAVOR_PROFILE_PROMPT = PromptTemplate(
    template=_template, input_variables=["question", "context"]
)