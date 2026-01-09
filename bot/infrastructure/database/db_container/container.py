class Container:

    def __init__(self, session,
                 user_service,
                 user_repo,
                 user_model,
                 book_service,
                 book_repo,
                 book_model,
                 reading_service,
                 reading_repo,
                 reading_model,
                 book_content_service,
                 book_content_repo,
                 book_content_model,
                 ) -> None:
        self._session = session
        self._user_service = user_service
        self._user_repo = user_repo
        self._user_model = user_model
        self._book_service = book_service
        self._book_repo = book_repo
        self._book_model = book_model
        self._reading_service = reading_service
        self._reading_repo = reading_repo
        self._reading_model = reading_model
        self._book_content_service = book_content_service
        self._book_content_repo = book_content_repo
        self._book_content_model = book_content_model
      

    @property
    def session(self):
        return self._session

    @property
    def user_service(self):
        return self._user_service(
            self._user_repo(
                self._session,
                self._user_model
            )
        )
        
    @property
    def book_service(self):
        return self._book_service(
            self._book_repo(
                self._session,
                self._book_model
            )
        )
        
    @property
    def reading_service(self):
        return self._reading_service(
            self._reading_repo(
                self._session,
                self._reading_model
            )
        )
        
    @property
    def book_content_service(self):
        return self._book_content_service(
            self._book_content_repo(
                self._session,
                self._book_content_model
            )
        )