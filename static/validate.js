Vue.use(VeeValidate, {
    locale: 'ja',
    dictionary: {
        ja: {
            messages: {
                required: (field) => `${field}を入力してください`,
                max_value: (field, [length]) => `${field}は${length}以内にしてください`,
                min_value: (field, [length]) => `${field}は${length}以上にしてください`,
            }
        }
    }
});