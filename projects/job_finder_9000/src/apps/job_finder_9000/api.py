from ninja import Router

router = Router(
    tags=["Job_finder_9000"],
)


@router.get("/additonal endpoint")
def get_job_finder_9000(request):
    return {"message": "Hello, World!"}
