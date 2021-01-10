var search = new Vue({
    el: "#search-result",
    data: {
        isLoading: false,
        searchResult: "",
        isEmptyDisabled: false
    },
    delimiters: ["${", "}$"]
})

var form = new Vue({
    el: "#search-form",
    data: {
            errors: [],
            availableErrors: [
                "List of cards cannot be empty",
                "List cannot be longer than 15 cards",
                "Card name cannot be empty",
                "Card name cannot be shorter than 3 symbols"
            ],
            cards: "",
            cardsList: [],
            allowEmpty: "",
            allowArt: ""
    },
    methods: {
        flushErrors: function (e) {
            this.errors = []
        },
        checkForm: function (e) {
            this.cardsList = this.cards.split(/\r?\n/);

            if (!this.cardsList.length && !this.errors.indexOf(this.availableErrors[0])) {
                this.errors.push(this.availableErrors[0]);
                return
            }

            if (this.cardsList.length > 15 && !this.errors.indexOf(this.availableErrors[1])) {
                this.errors.push(this.availableErrors[1]);
            }

           for (item of this.cardsList) {
                if (/^ *$/.test(item) && !this.errors.indexOf(this.availableErrors[2])) {
                    this.errors.push(this.availableErrors[2]);
                }
                else if (item.length < 3 && !this.errors.indexOf(this.availableErrors[3])) {
                    this.errors.push(this.availableErrors[3]);
                }
            };
            
        },
        getSearch: function (e) {
            this.flushErrors();
            this.checkForm();

            if (this.errors.length)
                return;
            
            search.isLoading = true;
            search.searchResult = "";

            axios
                .post(
                    "/search", 
                    {
                        cards: this.cardsList,
                        allow_empty: this.allowEmpty || false,
                        allow_art: this.allowArt || false
                    }
                )
                .then(
                    function (response) {
                        search.isLoading = false;
                        search.searchResult = response.data;
                    }
                );
        }
    },
    delimiters: ["${", "}$"]
})