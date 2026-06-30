-- Descrição do procedure

SET search_path TO plataforma;

CREATE OR REPLACE PROCEDURE cancelar_tarefa(
    IN in_executado_por INT,       -- Sempre primeiro
    IN in_tarefa_id INT,
    IN in_param INT,
    IN in_param2 TEXT,
    IN in_cancelar_inscricoes BOOL DEFAULT FALSE
)
LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_grupo_id BIGINT;
BEGIN
    -- Buscar o ID do grupo a partir da tarefa
    SELECT o.grupo INTO v_grupo_id
    FROM tarefa t
    JOIN ocorreu o ON o.id = t.ocorrencia
    WHERE t.id = in_tarefa_id;

    -- Verificar permissão de coordenação para este grupo
    PERFORM plataforma.verificar_permissao(in_executado_por, 'coordenação', v_grupo_id);

    --------------------------------------------------------------------
    -- 1. Cancelar a tarefa (valido = FALSE)
    --------------------------------------------------------------------
    UPDATE tarefa
    SET valido = FALSE,
        atualizado = NOW()
    WHERE id = in_tarefa_id;

    --------------------------------------------------------------------
    -- 2. Cancelar inscrições se solicitado
    --------------------------------------------------------------------
    IF in_cancelar_inscricoes THEN
    UPDATE executou
    SET valido = FALSE
    WHERE tarefa = in_tarefa_id;
    END IF;


    --------------------------------------------------------------------
    -- 3. Registrar LOG
    --------------------------------------------------------------------
    INSERT INTO log (rotulo, dados)
    VALUES (
        'cancelar_tarefa',
        jsonb_build_object(
            'executado_por', in_executado_por,
            'tarefa_id', in_tarefa_id,
            'cancelar_inscricoes', in_cancelar_inscricoes,
            'param1', in_param,
            'param2', in_param2
        )
    );

END;
$procedure$;
