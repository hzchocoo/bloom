from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    topic: str
    prompt: str
    options: tuple[str, str, str, str]
    correct: int
    explanation: str
    source_quote: str = ""


QUESTIONS = (
    Question(
        "Version control",
        "What does a Git commit record?",
        ("A snapshot of the project's staged contents", "A live server's CPU usage",
         "A list of open browser tabs", "A new production deployment"),
        0,
        "A commit records a project snapshot from the staging area so you can trace changes over time.",
    ),
    Question(
        "Continuous integration",
        "What is a common job for a continuous integration pipeline?",
        ("Manually approve every code edit", "Run automated tests on code changes",
         "Archive all production logs", "Assign passwords to developers"),
        1,
        "Running tests as changes are integrated helps the team spot failures early.",
    ),
    Question(
        "Containers",
        "Which Docker artifact is used as the template for a container?",
        ("A volume", "A network", "An image", "A build log"),
        2,
        "A Docker image bundles the application and its dependencies. Docker uses it to create a container.",
    ),
    Question(
        "Observability",
        "Which signal would help you see whether request latency rose after a deployment?",
        ("The number of branches in Git", "The size of the README",
         "The names of the build jobs", "A chart of request duration over time"),
        3,
        "Request duration metrics let you compare latency before and after a deployment.",
    ),
    Question(
        "Infrastructure as code",
        "Why define infrastructure in version-controlled files?",
        ("To review changes and recreate environments consistently",
         "To make servers run without an operating system",
         "To remove the need to monitor services",
         "To guarantee that deployments never fail"),
        0,
        "Versioned definitions let a team review changes and apply the same configuration across environments.",
    ),
)
