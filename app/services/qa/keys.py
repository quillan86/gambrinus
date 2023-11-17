

class RetrievalKeys:
    irrelevant_intent: str = 'off topic'
    intents: list[str] = ['general knowledge', 'flavor profiling', 'ingredient substitution',
                          'allergen identification', 'ingredient pairing',
                          'recipe formulation', 'style guidelines', 'recipe scaling']
    vectordb_intents: list[str] = ['general knowledge']
    unimplemented_intents: list[str] = ['ingredient substitution',
                                        'allergen identification', 'ingredient pairing',
                                        'recipe formulation', 'recipe scaling']
    sem_intents: list[str] = []
#    sem_intents: list[str] = ['flavor profiling', 'ingredient substitution']
    passthrough_intents: list[str] = ['general knowledge',
                                      'allergen identification', 'ingredient pairing']
    out_of_scope_intents: list[str] = ['recipe formulation', 'style guidelines', 'recipe scaling']
    flavor_intent: list[str] = ['flavor profiling', 'style guidelines']



retrieval_keys = RetrievalKeys()
