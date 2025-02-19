class ContextRecommender(object):
    """Interface for context recommender classes."""
    def __init__(self):
        raise NotImplementedError

    def get_n_contexts(self):
        raise NotImplementedError

    def get_top_context(self):
        raise NotImplementedError
