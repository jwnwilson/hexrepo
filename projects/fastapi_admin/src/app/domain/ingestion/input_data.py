from pydantic import BaseModel


class InputData(BaseModel):
    entity_id: str | None = None
    row_id: str
    source: str
    scraper_name: str
    wallets: list[str] = []
    emails: list[str] = []
    phones: list[str] = []
    ibans: list[str] = []
    platforms: list[str] = []
    credit_cards: list[str] = []
    names: list[str] = []
    ip_addresses: list[str] = []
    countries: list[str] = []
    currencies: list[str] = []
    usernames: list[str] = []
    profile_links: list[str] = []

    @property
    def pii(self) -> list[str]:
        return [
            item
            for field in [
                self.wallets,
                self.emails,
                self.phones,
                self.ibans,
                self.credit_cards,
                self.names,
                self.ip_addresses,
                self.usernames,
                self.profile_links,
            ]
            for item in field
        ]

    def __add__(self, other: "InputData") -> "InputData":
        return InputData(
            row_id=self.row_id,
            source=self.source,
            scraper_name=self.scraper_name,
            wallets=list(set(self.wallets + other.wallets)),
            emails=list(set(self.emails + other.emails)),
            phones=list(set(self.phones + other.phones)),
            ibans=list(set(self.ibans + other.ibans)),
            platforms=list(set(self.platforms + other.platforms)),
            credit_cards=list(set(self.credit_cards + other.credit_cards)),
            names=list(set(self.names + other.names)),
            ip_addresses=list(set(self.ip_addresses + other.ip_addresses)),
            countries=list(set(self.countries + other.countries)),
            currencies=list(set(self.currencies + other.currencies)),
            usernames=list(set(self.usernames + other.usernames)),
            profile_links=list(set(self.profile_links + other.profile_links)),
        )
