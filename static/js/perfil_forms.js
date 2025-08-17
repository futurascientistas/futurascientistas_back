function setErrorMessage(field, message) { 
    let errorElement = field.nextElementSibling;
    if (!errorElement || !errorElement.classList.contains("error-message")) {
        errorElement = document.createElement("span");
        errorElement.className = "text-red-500 text-sm mt-1 error-message";
        field.parentNode.insertBefore(errorElement, field.nextElementSibling);
    }
    errorElement.textContent = message;
}

function clearAllErrors(stepId) {
    const stepDiv = document.getElementById(stepId);
    if (!stepDiv) return;
    const errorElements = stepDiv.querySelectorAll('.error-message');
    errorElements.forEach(el => el.textContent = '');
}

function clearTableErrors() {
    document.querySelectorAll('#notas-table-body .error-row').forEach(el => el.remove());
}

function appendRowErrorAfter(row, message) {
    if (!row) return;
    const next = row.nextElementSibling;
    if (next && next.classList.contains('error-row')) next.remove();

    const tr = document.createElement('tr');
    tr.className = 'error-row';
    const td = document.createElement('td');
    td.colSpan = row.children.length || 4;
    td.className = 'text-red-500 text-sm p-2';
    td.textContent = message;
    tr.appendChild(td);
    row.insertAdjacentElement('afterend', tr);
}

function appendTableErrorAtEnd(message) {
    const tbody = document.getElementById('notas-table-body');
    if (!tbody) return;
    const refRow = tbody.querySelector('.form-row');
    const tr = document.createElement('tr');
    tr.className = 'error-row';
    const td = document.createElement('td');
    td.colSpan = (refRow?.children.length) || 4;
    td.className = 'text-red-500 text-sm p-2';
    td.textContent = message;
    tr.appendChild(td);
    tbody.appendChild(tr);
}

function validateRequiredFields(stepId) {
    const stepDiv = document.getElementById(stepId);
    if (!stepDiv) return true;

    const requiredFields = stepDiv.querySelectorAll('[required]:not([style*="display: none"])');
    let isValid = true;

    requiredFields.forEach(field => {
        if (field.tagName === 'SELECT' && field.value === '') {
            setErrorMessage(field, "Este campo é obrigatório.");
            isValid = false;
        } else if (!field.value.trim()) {
            setErrorMessage(field, "Este campo é obrigatório.");
            isValid = false;
        } else {
            setErrorMessage(field, "");
        }
    });

    return isValid;
}

function validateCep(inputName) {
    const cepInput = document.querySelector(`input[name="${inputName}"]`);
    if (!cepInput) return true;

    if (cepInput.closest('.form-step').classList.contains('hidden')) {
        return true;
    }

    const cepValue = cepInput.value.replace(/\D/g, '');
    const hasLetters = /[a-zA-Z]/.test(cepInput.value);

    if (cepValue === '' && !cepInput.required) {
        setErrorMessage(cepInput, "");
        return true;
    }

    if (hasLetters || cepValue.length !== 8) {
        setErrorMessage(cepInput, "O CEP deve conter 8 dígitos e apenas números.");
        return false;
    }
    setErrorMessage(cepInput, "");
    return true;
}

function validatePhoneFields() {
    const phoneFields = document.querySelectorAll('input[name*="telefone"], input[name*="celular"]');
    let isValid = true;
    const phoneRegex = /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/;

    phoneFields.forEach((field) => {
        if (field.closest('.form-step').classList.contains('hidden')) {
            return;
        }

        let errorElement = field.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains("error-message")) {
            errorElement = document.createElement("span");
            errorElement.className = "text-red-500 text-sm mt-1 error-message";
            field.parentNode.insertBefore(errorElement, field.nextElementSibling);
        }

        if (field.required && field.value.trim() === "") {
            errorElement.textContent = "Este campo é obrigatório.";
            field.classList.add("border-red-500");
            isValid = false;
        } else if (field.value.trim() !== "" && !phoneRegex.test(field.value)) {
            errorElement.textContent = "Formato de telefone inválido. Use (##) 9####-#### ou (##) ####-####.";
            field.classList.add("border-red-500");
            isValid = false;
        } else {
            errorElement.textContent = "";
            field.classList.remove("border-red-500");
        }
    });
    return isValid;
}

function setupCepAutocomplete(cepInput, prefix = '') {
    if (!cepInput) {
        return;
    }

    cepInput.addEventListener('blur', async () => {
        let cep = cepInput.value.replace(/\D/g, '');

        if (cep.length !== 8) {
            return;
        }

        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            if (!response.ok) {
                throw new Error('Erro na consulta do CEP');
            }

            const data = await response.json();
            if (data.erro) {
                alert('CEP não encontrado.');
                return;
            }

            const rua = document.querySelector(`input[name="${prefix}rua"]`);
            const bairro = document.querySelector(`input[name="${prefix}bairro"]`);
            const cidade = document.querySelector(`select[name="${prefix}cidade"], input[name="${prefix}cidade"]` );
            const estado = document.querySelector(`select[name="${prefix}estado"], input[name="${prefix}estado"]`);
            const numero = document.querySelector(`input[name="${prefix}numero"]`);

            if (rua) rua.value = data.logradouro || '';
            if (bairro) bairro.value = data.bairro || '';
            
            if (estado && estado.tagName === 'SELECT') {
                const uf = data.uf;
                const option = Array.from(estado.options).find(opt => opt.textContent.includes(uf));
                 
                if (option) {
                    estado.value = option.value;
                } else {
                    console.warn(`Opção para o estado "${uf}" não encontrada.`);
                }
            }

            if (cidade && cidade.tagName === 'SELECT') {
                const localidade = data.localidade;
                const uf = data.uf;
                const textoCompleto = `${localidade} - ${uf}`;
                
                const option = Array.from(cidade.options).find(opt => opt.textContent.trim() === textoCompleto);
                
                if (option) {
                    cidade.value = option.value;
                } else {
                    console.warn(`Opção para a cidade "${textoCompleto}" não encontrada.`);
                }
            }

            
            if (numero) numero.focus();
        } 
        catch (error) {
            console.error(error);
            alert('Não foi possível buscar o endereço pelo CEP.');
        }
    });
}

let disciplinaOptions = [];

async function fetchDisciplinas() {
    try {
        const response = await fetch('/api/disciplinas/');
        if (!response.ok) {
            throw new Error('Erro ao buscar disciplinas da API.');
        }
        const data = await response.json();
        disciplinaOptions = data;
    } catch (error) {
        console.error("Erro ao carregar disciplinas:", error);
        alert("Não foi possível carregar as disciplinas. Tente novamente mais tarde.");
    }
}

function populateDisciplinaSelect(selectElement, selectedValue = null) {
    while (selectElement.options.length > 0) {
        selectElement.remove(0);
    }

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Selecione uma disciplina';
    selectElement.appendChild(defaultOption);

    disciplinaOptions.forEach(disciplina => {
        const option = document.createElement('option');
        option.value = disciplina.id;
        option.textContent = disciplina.nome;
        if (selectedValue !== null && String(disciplina.id) === String(selectedValue)) {
            option.selected = true;
        }
        selectElement.appendChild(option);
    });
}

function updateElementIndex(el, prefix, new_index) {
    const id_regex = new RegExp('(' + prefix + '-\\d+-)|(' + prefix + '-__prefix__-)');
    const replacement = prefix + '-' + new_index + '-';

    if (el.getAttribute('for')) {
        el.setAttribute('for', el.getAttribute('for').replace(id_regex, replacement));
    }
    if (el.id) {
        el.id = el.id.replace(id_regex, replacement);
    }
    if (el.name) {
        el.name = el.name.replace(id_regex, replacement);
    }
}

window.adicionarFormularioComDisciplinas = function() {
    const notasTableBody = document.getElementById('notas-table-body');
    const emptyFormTemplate = document.getElementById('empty-form-template');
    
    if (!emptyFormTemplate) {
        console.error("Template 'empty-form-template' não encontrado!");
        return;
    }

    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]'); 
    if (!totalFormsInput) {
        console.error("TOTAL_FORMS input não encontrado!");
        return;
    }

    let formIdx = parseInt(totalFormsInput.value);

    const newFormRow = emptyFormTemplate.content.cloneNode(true);
    const formRowElement = newFormRow.querySelector('.form-row');

    const formsetPrefix = window.formsetPrefix || 'notas';

    formRowElement.querySelectorAll('[id*="__prefix__"], [name*="__prefix__"]').forEach(function(el) {
        updateElementIndex(el, formsetPrefix, formIdx);
    });

    notasTableBody.appendChild(formRowElement);

    const newDisciplinaSelect = formRowElement.querySelector(`select[name="${formsetPrefix}-${formIdx}-disciplina"]`);
    if (newDisciplinaSelect) {
        populateDisciplinaSelect(newDisciplinaSelect);
    }

    totalFormsInput.value = formIdx + 1;
};

window.removerForm = function(button) {
    const row = button.closest('.form-row');
    if (!row) return;

    const deleteInput = row.querySelector('input[name$="-DELETE"]');
    if (deleteInput) {
        deleteInput.checked = true;
        row.classList.add('hidden');
    } else {
        row.remove();
        const totalFormsInput = document.querySelector(`input[name="${formsetPrefix}-TOTAL_FORMS"]`);
        totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
    }
};

function setupSubmitButton() {
    const checkbox = document.getElementById('id_autodeclaracao');
    const submitButton = document.getElementById('submit-step-6');

    if (checkbox && submitButton) {
        function toggleSubmitButton() {
            submitButton.disabled = !checkbox.checked;
        }

        checkbox.addEventListener('change', toggleSubmitButton);
        toggleSubmitButton();
    }
}

function goToStep(step) {
    document.querySelectorAll('.form-step').forEach(div => div.classList.add('hidden'));
    document.getElementById('step-' + step).classList.remove('hidden');

    const currentStepInput = document.getElementById('current-step-input');
    if (currentStepInput) {
        currentStepInput.value = step;
    }
    
    document.querySelectorAll('.step-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.step) === step) {
            item.classList.add('active');
        }
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (step === 2) {
        const cepInputUser = document.querySelector('input[name="cep"]');
        if (cepInputUser) setupCepAutocomplete(cepInputUser);
    } else if (step === 3) {
        const cepInputEscola = document.querySelector('input[name="endereco_escola-cep"]');
        if (cepInputEscola) setupCepAutocomplete(cepInputEscola, 'endereco_escola-');
    }
}

function validateAndAdvance(event) {
    const currentStep = parseInt(document.getElementById('current-step-input').value);
    let isStepValid = true;

    clearAllErrors(`step-${currentStep}`);

    if (currentStep === 1) {
        if (!validateRequiredFields('step-1')) isStepValid = false;
        if (!validatePhoneFields()) isStepValid = false;
    } else if (currentStep === 2) {
        if (!validateRequiredFields('step-2')) isStepValid = false;
        if (!validateCep('cep')) isStepValid = false;
    } else if (currentStep === 3) {
        if (!validateRequiredFields('step-3')) isStepValid = false;
        if (!validateCep('endereco_escola-cep')) isStepValid = false;
        if (!validatePhoneFields()) isStepValid = false;
    } else if (currentStep === 5) {
        const notasTableBody = document.getElementById('notas-table-body');
        const notaRows = notasTableBody ? notasTableBody.querySelectorAll('.form-row:not(.hidden)') : [];
        let disciplinaMap = {};

        clearTableErrors();
        document.querySelectorAll('#step-5 .error-message').forEach(el => el.textContent = '');
        document.querySelectorAll('#step-5 .border-red-500').forEach(el => el.classList.remove('border-red-500'));

        notaRows.forEach(row => {
            const disciplinaSel = row.querySelector('select[name$="-disciplina"]');
            const bimestreSel   = row.querySelector('select[name$="-bimestre"]');
            const valorInput    = row.querySelector('input[name$="-valor"]');

            const missing = [];
            if (!disciplinaSel?.value) { missing.push('disciplina'); disciplinaSel?.classList.add('border-red-500'); }
            if (!bimestreSel?.value)   { missing.push('bimestre'); bimestreSel?.classList.add('border-red-500'); }
            if (!valorInput?.value)    { missing.push('nota'); valorInput?.classList.add('border-red-500'); }

            if (missing.length) {
                appendRowErrorAfter(row, `Preencha ${missing.join(', ')}.`);
                isStepValid = false;
            }

            const discValue = disciplinaSel?.value;
            const bimValue  = bimestreSel?.value;
            if (discValue) {
                if (!disciplinaMap[discValue]) disciplinaMap[discValue] = new Set();
                if (bimValue) disciplinaMap[discValue].add(String(bimValue));
            }
        });

        if (!disciplinaOptions || disciplinaOptions.length === 0) {
            appendTableErrorAtEnd("Não há disciplinas configuradas no sistema.");
            isStepValid = false;
        } else {
            disciplinaOptions.forEach(disciplina => {
                const bimestres = disciplinaMap[disciplina.id] || new Set();
                const tem1 = bimestres.has("1");
                const tem2 = bimestres.has("2");

                if (!(tem1 && tem2)) {
                    const anchor = Array.from(notaRows).reverse().find(r =>
                        r.querySelector('select[name$="-disciplina"]')?.value === String(disciplina.id)
                    );
                    const msg = `A disciplina ${disciplina.nome} precisa ter notas para o 1º e 2º bimestre.`;
                    if (anchor) appendRowErrorAfter(anchor, msg);
                    else appendTableErrorAtEnd(msg);

                    isStepValid = false;
                }
            });
        }
    }

    if (!isStepValid) {
        event.preventDefault();
        const firstInvalidField = document.querySelector(`#step-${currentStep} .error-message:not(:empty)`);
        if (firstInvalidField) {
            firstInvalidField.previousElementSibling?.focus();
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchDisciplinas(); 

    const urlParams = new URLSearchParams(window.location.search);
    const stepInUrl = parseInt(urlParams.get('step')) || 1;
    goToStep(stepInUrl); 

    document.querySelectorAll('#notas-table-body select[name$="-disciplina"]').forEach(selectElement => {
        const initialValue = selectElement.value;
        populateDisciplinaSelect(selectElement, initialValue);
    });

    setupSubmitButton(); 

    document.querySelectorAll('button[data-navigation]').forEach(button => {
        if (button.textContent.trim().toLowerCase() === 'voltar') {
            button.addEventListener('click', () => {
                const step = parseInt(button.dataset.navigation);
                goToStep(step);
            });
        }
    });

    document.getElementById('perfil-form').addEventListener('submit', validateAndAdvance);

    const addButton = document.getElementById('add-nota-button'); 
    if (addButton) {
        addButton.addEventListener('click', adicionarFormularioComDisciplinas);
    }
    
    const notasTableBody = document.getElementById('notas-table-body');
    if (notasTableBody) {
        notasTableBody.addEventListener('click', (event) => {
            const removerButton = event.target.closest('.remover-nota-button');
            if (removerButton) removerForm(removerButton);
        });
    }
});
