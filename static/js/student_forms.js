document.addEventListener('DOMContentLoaded', () => {

  const formEl = document.getElementById('student-form');
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const cidadeField = document.getElementById('id_cidade');
  const estadoField = document.getElementById('id_estado');
  const projetoSelect = document.getElementById('id_projeto');
  const cepField = document.getElementById('id_cep');
  const ruaField = document.getElementById('id_rua');
  const bairroField = document.getElementById('id_bairro');
  const numeroField = document.getElementById('id_numero');

  // ---------- Upload Automático de Arquivos ----------
  formEl.addEventListener('change', async (event) => {
    const fileInput = event.target.closest('.file-upload-input');
    if (!fileInput || !fileInput.files || !fileInput.files.length) return;

    const fieldName = fileInput.name;
    const formData = new FormData();
    formData.append('auto_upload_field', fieldName);
    formData.append(fieldName, fileInput.files[0]);

    try {
      const response = await fetch(window.location.href, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        console.error('Resposta de erro:', data);
        alert(data.error || 'Erro ao enviar arquivo.');
        return;
      }

      const wrapper = fileInput.closest('.file-upload-wrapper');
      if (wrapper && data.html) {
        wrapper.outerHTML = data.html;
      } else {
        window.location.reload();
      }

    } catch (err) {
      console.error('Erro no upload:', err);
      alert('Erro inesperado ao enviar o arquivo. Verifique sua conexão e tente novamente.');
    }
  });

  formEl.addEventListener('click', async (event) => {
    const clearButton = event.target.closest('.js-clear-button');
    if (clearButton) {
      event.preventDefault();

      const clearFieldName = clearButton.getAttribute('data-clear-target'); 
      console.log("Campo de remoção (clear field) alvo:", clearFieldName);

      const formData = new FormData();
      formData.append('auto_clear_field', clearFieldName);

      try {
        const response = await fetch(window.location.href, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken },
          body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
          console.error('Resposta de erro:', data);
          alert(data.error || 'Erro ao remover arquivo.');
          return;
        }

        const wrapper = clearButton.closest('.file-upload-wrapper');
        if (wrapper && data.html) {
          wrapper.outerHTML = data.html; // substitui pelo campo atualizado
        } else {
          window.location.reload();
        }

      } catch (err) {
        console.error('Erro no auto-clear:', err);
        alert('Erro inesperado ao remover o arquivo. Verifique sua conexão.');
      }
    }
  });

  // ---------- Autocomplete CEP via ViaCEP API ----------
  const buscarCep = async (cep) => {
    if (cep.length !== 8) return;

    try {
      const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      if (!response.ok) throw new Error('Erro na consulta do CEP');

      const data = await response.json();
      if (data.erro) {
        alert('CEP não encontrado.');
        return;
      }

      if (ruaField) ruaField.value = data.logradouro || '';
      if (bairroField) bairroField.value = data.bairro || '';

      if (estadoField && estadoField.tagName === 'SELECT') {
        const option = Array.from(estadoField.options).find(opt => opt.textContent.includes(data.uf));
        if (option) {
          estadoField.value = option.value;
          estadoField.dispatchEvent(new Event('change'));
        }
      }

      if (cidadeField && cidadeField.tagName === 'SELECT') {
        const localidade = data.localidade.trim().toLowerCase();
        const option = Array.from(cidadeField.options).find(opt => opt.textContent.toLowerCase().includes(localidade));
        if (option) {
          cidadeField.value = option.value;
          cidadeField.dispatchEvent(new Event('change'));
        }
      }

      if (numeroField) numeroField.focus();
      filtrarProjetos();

    } catch (error) {
      console.error(error);
      alert('Não foi possível buscar o endereço pelo CEP. Por favor, preencha manualmente.');
    }
  };

  if (cepField) {
    cepField.addEventListener('blur', (e) => {
      buscarCep(e.target.value.replace(/\D/g, ''));
    });
  }

  // ---------- Filtro de Projetos por Estado/Cidade ----------
  const filtrarProjetos = () => {
    if (!projetoSelect || !estadoField || !cidadeField) return;

    const estadoId = estadoField.value;
    const cidadeId = cidadeField.value;

    Array.from(projetoSelect.options).forEach(option => {
      const optionEstadoId = option.dataset.estado;
      const optionCidadeId = option.dataset.cidade;

      const isDefaultOption = option.value === "";
      const isVisible = isDefaultOption || (optionEstadoId === estadoId && (optionCidadeId === "" || optionCidadeId === cidadeId));

      option.style.display = isVisible ? 'block' : 'none';
      option.disabled = !isVisible;
    });

    if (projetoSelect.value && !Array.from(projetoSelect.options).find(o => o.value === projetoSelect.value && o.style.display !== 'none')) {
      projetoSelect.value = '';
    }
  };

  if (estadoField) {
    estadoField.addEventListener('change', filtrarProjetos);
  }
  if (cidadeField) {
    cidadeField.addEventListener('change', filtrarProjetos);
  }

  // Chamada inicial
  filtrarProjetos();
});