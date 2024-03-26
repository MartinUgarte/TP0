package common 

import (
	"fmt"
	"strings"
)

const (
	FIELD_SEPARATOR = ","
	HEADER_SEPARATOR = "#"
)
type Bet struct {
	Agency	 string
	Name     string
	Surname  string
	Document string
	Birthday string
	Number   string
}

func NewBet(agency string, name string, surname string, document string, birthday string, number string) *Bet {
	return &Bet {
		Agency:   agency,
		Name:     name,
		Surname:  surname,
		Document: document,
		Birthday: birthday,
		Number:   number,
	}
}

func (b *Bet) Serialize() string {
	message := strings.Join([]string{b.Agency, b.Name, b.Surname, b.Document, b.Birthday, b.Number}, FIELD_SEPARATOR)
	header := len(message)
	return fmt.Sprintf("%d%s%s", header, HEADER_SEPARATOR, message)
}