from app.db.sqldb.services import user_service
from app.services.qa.followup import FollowupService
from app.services.qa.summary import SummaryService
from app.services.qa.agents.openai_function import OpenAIFunctionAgentService
from app.services.qa.tools import flavor_profiler_tool, pubmed_tool
from langchain.schema.messages import HumanMessage, AIMessage
import asyncio
import json

chat_history = [
    HumanMessage(content="How do I brew an American Lager"),
    AIMessage(content="""To brew an American Lager, you can follow this recipe:

American Lager Recipe:
- Malts: 80% Pilsner malt, 10% Flaked rice, 10% Corn syrup
- Hops: 1 oz Saaz hops (60 minutes), 0.5 oz Saaz hops (10 minutes)
- Yeast: American lager yeast
- Water: Use soft water with low mineral content
- Mash: Mash the grains at 150°F (65.5°C) for 60 minutes
- Boil: Boil the wort for 60 minutes, adding hops according to the schedule
- Fermentation: Ferment at a temperature of 50-55°F (10-13°C) for 2-3 weeks
- Carbonation: Carbonate to a medium level of carbonation (around 2.5 volumes of CO2)

Please note that this is a basic recipe and you can adjust the ingredients and process according to your preferences and brewing setup. Happy brewing!""")
]

agent = OpenAIFunctionAgentService(chat_history=[], max_iterations=5, user_id=1)

result = agent.run("What is the best quantum mechanics for a Lager?")

#result = json.loads(pubmed_tool._run("alcohol poisoning"))

print(result)

#summary = asyncio.run(SummaryService.run(chat_history))

#print(summary)

#answer = asyncio.run(IntentRetrievalService.run(question, intent='flavor profiling'))
#flavor_profile = asyncio.run(FlavorAlgorithmService.run(recipe))

#print(recipe)
#print(json.dumps(flavor_profile, indent=4))