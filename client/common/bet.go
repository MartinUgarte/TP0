package common 

import (
	"github.com/sirupsen/logrus"
	"fmt"
)

const (
	SEPARATOR = "\t"
	NEWLINE = "\n"
	END_HEADER = " "
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

func (b *Bet) Log() {
	logrus.Infof("Bet info | agency: %v | name: %v | surname: %v | document: %v | birthday: %v | number: %v",
		b.Agency,
		b.Name,
		b.Surname,
		b.Document,
		b.Birthday,
		b.Number,
	)
}

func (b *Bet) Serialize() string {
	message := b.Agency + SEPARATOR + b.Name + SEPARATOR + b.Surname + SEPARATOR + b.Document + SEPARATOR + b.Birthday + SEPARATOR + b.Number + NEWLINE
	header := len(message)
	return fmt.Sprintf("%d%s", header, message)
}