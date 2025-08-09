from ninja import Router

router = Router(
    tags=["aipet"],
)


@router.get("/additonal endpoint")
def get_aipet(request):
    return {"message": "Hello, World!"}
