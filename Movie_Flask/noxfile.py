import nox

@nox.session
def movie_booking_test_session(session):
    # Set up your test environment and dependencies here
    session.install("-r", "requirements.txt")
    session.install("pytest", "pytest-cov")
    session.install("pytest-html")
    session.install("mongomock")
    session.install("requests")
    
    # Run your tests
    session.run("pytest",
                "-vv",
                "--html=report.html",
                "--cov=app",
                "--cov-report=html",
                "--cov-report=xml",
                "--junitxml=tests/test_report.xml",
                env={
                    "PROD_MONGO_URI":"mongodb://localhost:27017/test"
                })

