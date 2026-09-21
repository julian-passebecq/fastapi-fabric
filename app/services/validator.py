from app.domain.models import PipelineDefinition, ValidationIssue, ValidationResult


def validate_pipeline(pipeline: PipelineDefinition) -> ValidationResult:
    issues: list[ValidationIssue] = []
    names = {activity.name for activity in pipeline.activities}

    if not pipeline.activities:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="EMPTY_PIPELINE",
                message="Pipeline has no activities.",
            )
        )

    for activity in pipeline.activities:
        for dependency in activity.depends_on:
            if dependency.activity not in names:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="UNKNOWN_DEPENDENCY",
                        message=f"Dependency '{dependency.activity}' does not exist.",
                        activity=activity.name,
                    )
                )
            if dependency.activity == activity.name:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="SELF_DEPENDENCY",
                        message="Activity cannot depend on itself.",
                        activity=activity.name,
                    )
                )

    graph = {a.name: [d.activity for d in a.depends_on if d.activity in names] for a in pipeline.activities}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dep in graph[node]:
            if visit(dep):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(visit(name) for name in graph if name not in visited):
        issues.append(
            ValidationIssue(
                severity="error",
                code="CYCLIC_DEPENDENCY",
                message="Pipeline dependency graph contains a cycle.",
            )
        )

    return ValidationResult(valid=not any(i.severity == "error" for i in issues), issues=issues)
