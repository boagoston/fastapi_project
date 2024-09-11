from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Category(Enum):
    TOOLS = "tools"
    CONSUMABLES = "consumables"

class Item(BaseModel):
    name: str
    price: float
    count: int
    id: int
    category: Category


items = {
    0: Item(name="Martelo", price=9.99, count=20, id=0,category=Category.TOOLS),
    1: Item(name="Alicate", price=5.99, count=20, id=1,category=Category.TOOLS),
    2: Item(name="Prego", price=2.99, count=10, id=2, category=Category.CONSUMABLES),
    3: Item(name="parafuso", price=3.99, count=15, id=3, category=Category.CONSUMABLES)
}

#FastAPI consegue lidar com serializaçãoi e deserialização para gente
#Nós podemos simplesmente usar tipos do python e pydantic, nesse caso dict[int, item]
@app.get("/")
def index() -> dict[str, dict[ int, Item]]:
    return{"items":items}


@app.get("/items/{item_id}")
def query_item_by_id(item_id:int) -> Item:
    if item_id not in items:
        raise HTTPException(
            status_code = 404, detail=f"item with {item_id=} não foi encontrado"
            )
    return items[item_id]

Selection = dict[
    str, str | int | float | Category | None
]

@app.get("/items/")
def query_item_by_parameters(
    name: str | None = None ,
    price: float | None = None,
    count: int | None = None,
    category: Category | None = None,
    ) -> dict [str, Selection | list[Item]]:

    def check_item(item: Item):
        return all(
            (
                name is None or item.name == name,
                price is None or item.price == price,
                count is None or item.count != count,
                category is None or item.category is category,
            )
        )
    
    selection = [item for item in items.values() if check_item(item)]
    return {
        "query": {"name": name, "price": price, "count": count, "category": category},
        "selection": selection,
    }

@app.post("/")
def add_item(item:Item) -> dict[str, Item]:

    if item.id in items:
        HTTPException(status_code=400, detail=f"Item com {item.id=} já existe.")
    
    items[item.id] = item
    return {"adicionado": item}


@app.put ("/update/{item_id}")
def update(
    item_id: int,
    name: str | None = None,
    price: float | None = None,
    count: int | None = None,
) -> dict[str, Item]:
    
    if item_id not in items:
            HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (name, price, count)):
        raise HTTPException(
            status_code=400, detail="No parameters provided for update."
        )

    item = items[item_id]
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if count is not None:
        item.count = count

    return {"updated": item}

@app.delete("/delete/{item_id}")
def delete_item(item_id:int) -> dict[str,Item]:

    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item com {item_id=} não existe.")
    
    item = items.pop(item_id)
    return {"deleted": item}


