from typing import List, Optional

from app import oauth2
from .. import models, schemas, oauth2
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)

# Get all accounts in the mastodon_accts table, paginated, searchable by username. returns a list of schemas.MastodonUserResponse
@router.get("/", response_model=List[schemas.MastodonUserResponse], description="Get all accounts (paginated) (searchable by username) [must be logged in]")
async def get_accounts(db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    results = db.query(models.MastodonAccts).group_by(models.MastodonAccts.id).filter(models.MastodonAccts.acct.contains(search)).limit(limit).offset(skip).all()
    return results

# Get account by ID. returns a schemas.MastodonUserResponse
@router.get("/{id}", response_model=schemas.MastodonUserResponse, description="Get account by ID [must be logged in]")
async def get_account(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    result = db.query(models.MastodonAccts).filter(models.MastodonAccts.id == id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {str(id)} was not found")
    return result

# Add a new account to the mastodon_accts table. returns a schemas.MastodonUserResponse
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.MastodonUserResponse, description="Add a new account [must be logged in]")
async def create_account(account: schemas.MastodonUserCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    try:
        new_account = models.MastodonAccts(**account.dict())
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return new_account
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Account {str(account.acct)} already exists")

# Update an account in the mastodon_accts table. returns a schemas.MastodonUserResponse
@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.MastodonUserResponse, description="Update an account [must be logged in]")
async def update_account(id: int, account: schemas.MastodonUserResponse, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    result = db.query(models.MastodonAccts).filter(models.MastodonAccts.id == id)
    if not result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {str(id)} was not found")
    result.update(account.dict())
    db.commit()
    return result.first()

# Delete an account from the mastodon_accts table. returns a schemas.MastodonUserResponse
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete an account [must be logged in]")
async def delete_account(id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    result = db.query(models.MastodonAccts).filter(models.MastodonAccts.id == id)
    if not result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {str(id)} was not found")
    result.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
