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
                    estado.dispatchEvent(new Event('change'));
                } else {
                    console.warn(`Opção para o estado "${uf}" não encontrada.`);
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

async function fetchCidadesPorEstado(estadoId) {
    try {
        const response = await fetch(`/api/cidades/?estado=${estadoId}`);
        if (!response.ok) {
            throw new Error('Erro ao buscar cidades da API.');
        }
        return await response.json();
    } catch (error) {
        console.error("Erro ao carregar cidades:", error);
        return [];
    }
}

function populateCidadeSelect(selectElement, cidades, selectedValue = null) {
    selectElement.innerHTML = '';
    
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Selecione uma cidade';
    selectElement.appendChild(defaultOption);

    cidades.forEach(cidade => {
        const option = document.createElement('option');
        option.value = cidade.id;
        option.textContent = cidade.nome_completo; 
        if (selectedValue !== null && String(cidade.id) === String(selectedValue)) {
            option.selected = true;
        }
        selectElement.appendChild(option);
    });
}

function setupCidadeAutocomplete(prefix = '') {
    const estadoSelect = document.querySelector(`select[name="${prefix}estado"]`);
    const cidadeSelect = document.querySelector(`select[name="${prefix}cidade"]`);

    if (!estadoSelect || !cidadeSelect) {
        return;
    }

    estadoSelect.addEventListener('change', async () => {
        const estadoId = estadoSelect.value;
        if (estadoId) {
            cidadeSelect.disabled = true;
            cidadeSelect.innerHTML = '<option>Carregando...</option>';

            const cidades = await fetchCidadesPorEstado(estadoId);
            populateCidadeSelect(cidadeSelect, cidades);

            cidadeSelect.disabled = false;
        } else {
            cidadeSelect.innerHTML = '<option value="">Selecione um estado primeiro</option>';
        }
    });

    const initialEstadoId = estadoSelect.value;
    if (initialEstadoId) {
        const initialCidadeId = cidadeSelect.value;
        fetchCidadesPorEstado(initialEstadoId).then(cidades => {
            populateCidadeSelect(cidadeSelect, cidades, initialCidadeId);
        });
    }
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
    showLoading();
    setTimeout(() => {
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
            setupCidadeAutocomplete();
            const cepInputUser = document.querySelector('input[name="cep"]');
            if (cepInputUser) setupCepAutocomplete(cepInputUser);
        } else if (step === 3) {
            setupCidadeAutocomplete('endereco_escola-');
            const cepInputEscola = document.querySelector('input[name="endereco_escola-cep"]');
            if (cepInputEscola) setupCepAutocomplete(cepInputEscola, 'endereco_escola-');
        }
        
        hideLoading();
    },100);
    
}

function validateAndAdvance(event) {
    const currentStep = parseInt(document.getElementById('current-step-input').value);
    let isStepValid = true;

    clearAllErrors(`step-${currentStep}`);

    if (document.getElementById("auto-upload-flag").value === "1") {
        return true;
    }

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
        const notaRows = document.querySelectorAll('#step-5 .form-row');
        let isValidStep = true;

        notaRows.forEach(row => {
            const valorInput = row.querySelector('input[name$="-nota_original"]');
            if (valorInput && !valorInput.value.trim()) {
                valorInput.classList.add('border-red-500');
                isValidStep = false;
            }
        });

        if (!isValidStep) {
            event.preventDefault();
            hideLoading();
            return;
        }
    }


    if (!isStepValid) {
        event.preventDefault();
        hideLoading();
        const firstInvalidField = document.querySelector(`#step-${currentStep} .error-message:not(:empty)`);
        if (firstInvalidField) {
            firstInvalidField.previousElementSibling?.focus();
        }
    }
}

function showLoading() {
    document.getElementById('loading-overlay')?.classList.remove('hidden');
}
function hideLoading() {
    document.getElementById('loading-overlay')?.classList.add('hidden');
}

function submitAutoUploadForm() {
    const form = document.getElementById("perfil-form");
    if (form) {
        document.getElementById("auto-upload-flag").value = "1";
        showLoading();
        form.submit();
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

    // ✅ Ajustado: reset do auto-upload flag nos submits de step
    document.querySelectorAll('button[type="submit"][name="submit_step"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const autoFlag = document.getElementById("auto-upload-flag");
            if (autoFlag) autoFlag.value = "0";
            showLoading();
        });
    });

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

    document.querySelectorAll('.file-upload-input').forEach(input => {
        input.addEventListener('change', submitAutoUploadForm);
    });

    document.querySelectorAll('.js-clear-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const targetName = this.getAttribute('data-clear-target');
            const hiddenInput = document.querySelector(`input[name="${targetName}"]`);

            if (hiddenInput) {
                hiddenInput.disabled = false;
                hiddenInput.checked = true;
                hiddenInput.value = "1";
                hiddenInput.dispatchEvent(new Event("change", { bubbles: true }));

                const autoFlag = document.getElementById("auto-upload-flag");
                if (autoFlag) autoFlag.value = "1";

                const form = this.closest('form');
                if (form) {
                    showLoading();
                    form.submit();
                }
            } else {
                console.warn("Input __clear não encontrado:", targetName);
            }
        });
    });

    document.getElementById("perfil-form").addEventListener("submit", () => {
        const clears = Array.from(document.querySelectorAll("input[name$='__clear']"));
        clears.forEach(c => {
            console.log("➡️ Enviando:", c.name, "checked:", c.checked, "value:", c.value);
        });
    });

    document.getElementById('perfil-form').addEventListener('submit', validateAndAdvance);

    document.getElementById("perfil-form").addEventListener("submit", () => {
        console.log("➡️ current_step:", document.getElementById("current-step-input").value);
        console.log("➡️ auto-upload-flag:", document.getElementById("auto-upload-flag").value);
    });

});