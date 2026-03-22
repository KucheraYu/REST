import uvicorn
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import (
    Session,
    declarative_base,
    joinedload,
    relationship,
)
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.types import Integer, String, Text

Base = declarative_base()
engine = create_engine(
    "sqlite:///lab2.db", connect_args={"check_same_thread": False}
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)

    posts = relationship(
        "PostModel", back_populates="author", cascade="all, delete-orphan"
    )


class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author = relationship("UserModel", back_populates="posts")
    comments = relationship(
        "CommentModel", back_populates="post", cascade="all, delete-orphan"
    )


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    post = relationship("PostModel", back_populates="comments")
    author = relationship("UserModel")


Base.metadata.create_all(bind=engine)


class CommentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    text: str
    post_id: int
    user_id: int


class PostOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    content: Optional[str] = None
    user_id: int
    comments: list[CommentOut] = []


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: str
    posts: list[PostOut] = []


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PostCreate(BaseModel):
    title: str
    content: Optional[str] = None
    user_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class CommentCreate(BaseModel):
    text: str
    post_id: int
    user_id: int


class CommentUpdate(BaseModel):
    text: str


class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    limit: int


app = FastAPI(
    title="Lab2 API",
    description="REST API — CRUD, pagination, sorting, filtering",
    version="1.0.0",
)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def _apply_sort(query, model, sort: Optional[str]):
    if sort is None:
        return query
    descending = sort.startswith("-")
    field_name = sort[1:] if descending else sort
    column = getattr(model, field_name, None)
    if column is None:
        raise HTTPException(400, f"Unknown sort field: {field_name}")
    return query.order_by(desc(column) if descending else asc(column))


def _get_or_404(db, model, pk):
    obj = db.query(model).get(pk)
    if obj is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return obj


# ── Users ────────────────────────────────────────────────────────

@app.get("/users", response_model=PaginatedResponse, tags=["Users"])
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(UserModel)
    if name:
        query = query.filter(UserModel.name.ilike(f"%{name}%"))
    query = _apply_sort(query, UserModel, sort)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return PaginatedResponse(
        data=[UserOut.model_validate(u) for u in items],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/users/{user_id}", response_model=UserOut, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = (
        db.query(UserModel)
        .options(joinedload(UserModel.posts).joinedload(PostModel.comments))
        .get(user_id)
    )
    if user is None:
        raise HTTPException(404, "User not found")
    return UserOut.model_validate(user)


@app.post("/users", response_model=UserOut, status_code=201, tags=["Users"])
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    user = UserModel(name=body.name, email=body.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@app.put("/users/{user_id}", response_model=UserOut, tags=["Users"])
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
):
    user = _get_or_404(db, UserModel, user_id)
    if body.name is not None:
        user.name = body.name
    if body.email is not None:
        user.email = body.email
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@app.delete("/users/{user_id}", status_code=204, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = _get_or_404(db, UserModel, user_id)
    db.delete(user)
    db.commit()


# ── Posts ────────────────────────────────────────────────────────

@app.get("/posts", response_model=PaginatedResponse, tags=["Posts"])
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PostModel)
    if user_id is not None:
        query = query.filter(PostModel.user_id == user_id)
    if title:
        query = query.filter(PostModel.title.ilike(f"%{title}%"))
    query = _apply_sort(query, PostModel, sort)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return PaginatedResponse(
        data=[PostOut.model_validate(p) for p in items],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/posts/{post_id}", response_model=PostOut, tags=["Posts"])
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(PostModel)
        .options(joinedload(PostModel.comments))
        .get(post_id)
    )
    if post is None:
        raise HTTPException(404, "Post not found")
    return PostOut.model_validate(post)


@app.post("/posts", response_model=PostOut, status_code=201, tags=["Posts"])
def create_post(body: PostCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).get(body.user_id) is None:
        raise HTTPException(400, "User not found")
    post = PostModel(title=body.title, content=body.content, user_id=body.user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostOut.model_validate(post)


@app.put("/posts/{post_id}", response_model=PostOut, tags=["Posts"])
def update_post(
    post_id: int,
    body: PostUpdate,
    db: Session = Depends(get_db),
):
    post = _get_or_404(db, PostModel, post_id)
    if body.title is not None:
        post.title = body.title
    if body.content is not None:
        post.content = body.content
    db.commit()
    db.refresh(post)
    return PostOut.model_validate(post)


@app.delete("/posts/{post_id}", status_code=204, tags=["Posts"])
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = _get_or_404(db, PostModel, post_id)
    db.delete(post)
    db.commit()


# ── Comments ─────────────────────────────────────────────────────

@app.get("/comments", response_model=PaginatedResponse, tags=["Comments"])
def list_comments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: Optional[str] = Query(None),
    post_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(CommentModel)
    if post_id is not None:
        query = query.filter(CommentModel.post_id == post_id)
    if user_id is not None:
        query = query.filter(CommentModel.user_id == user_id)
    query = _apply_sort(query, CommentModel, sort)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return PaginatedResponse(
        data=[CommentOut.model_validate(c) for c in items],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/comments/{comment_id}", response_model=CommentOut, tags=["Comments"])
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    return CommentOut.model_validate(_get_or_404(db, CommentModel, comment_id))


@app.post("/comments", response_model=CommentOut, status_code=201, tags=["Comments"])
def create_comment(body: CommentCreate, db: Session = Depends(get_db)):
    if db.query(PostModel).get(body.post_id) is None:
        raise HTTPException(400, "Post not found")
    if db.query(UserModel).get(body.user_id) is None:
        raise HTTPException(400, "User not found")
    comment = CommentModel(text=body.text, post_id=body.post_id, user_id=body.user_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentOut.model_validate(comment)


@app.put("/comments/{comment_id}", response_model=CommentOut, tags=["Comments"])
def update_comment(
    comment_id: int,
    body: CommentUpdate,
    db: Session = Depends(get_db),
):
    comment = _get_or_404(db, CommentModel, comment_id)
    comment.text = body.text
    db.commit()
    db.refresh(comment)
    return CommentOut.model_validate(comment)


@app.delete("/comments/{comment_id}", status_code=204, tags=["Comments"])
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = _get_or_404(db, CommentModel, comment_id)
    db.delete(comment)
    db.commit()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
