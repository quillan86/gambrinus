from langchain.output_parsers import GuardrailsOutputParser
from langchain.prompts import PromptTemplate
import os


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

beer_output_parser = GuardrailsOutputParser.from_rail(os.path.join(__location__, 'rail/style.xml'))

BEER_ENTITY_PROMPT = PromptTemplate(
    template=beer_output_parser.guard.base_prompt,
    input_variables=beer_output_parser.guard.prompt.variable_names,
)
