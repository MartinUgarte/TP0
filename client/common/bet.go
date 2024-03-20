package common 

import (
	"github.com/sirupsen/logrus"
)

type Bet struct {
	Name     string
	Surname  string
	Document string
	Birthday string
	Number   string
}

func NewBet(name string, surname string, document string, birthday string, number string) *Bet {
	return &Bet {
		Name:     name,
		Surname:  surname,
		Document: document,
		Birthday: birthday,
		Number:   number,
	}
}

func (b *Bet) LogBet() {
	logrus.Infof("Bet info | name: %v | surname: %v | document: %v | birthday: %v | number: %v",
		b.Name,
		b.Surname,
		b.Document,
		b.Birthday,
		b.Number,
	)
}