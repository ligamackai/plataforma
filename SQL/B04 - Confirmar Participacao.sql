SET search_path TO plataforma;

-- Descrição do procedure


CREATE OR REPLACE PROCEDURE confirmar_participacao(
  IN in_executado_por INT,  -- Todos os procedimentos devem receber este no primeiro parâmetro
  IN in_participou_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
   v_estado_atual   BOOLEAN;

   v_participante     INT;
   v_encontro       INT;

BEGIN
    -- Buscar o ID do grupo a partir da participação
    SELECT o.grupo INTO v_grupo_id
    FROM participou p
    JOIN encontro e ON e.id = p.encontro
    JOIN ocorreu o ON o.id = e.ocorrencia
    WHERE p.id = in_participou_id;

    -- Verificar permissão de coordenação para este grupo
    PERFORM plataforma.verificar_permissao(in_executado_por, 'coordenação', v_grupo_id);
    
    SELECT
        confirmado, participante, encontro
    INTO v_estado_atual, v_participante, v_encontro
    FROM participou
      WHERE id = in_participou_id;

          
    IF v_estado_atual is NULL THEN 
        RAISE EXCEPTION 'Nao encontrado';
    END IF;

    IF v_estado_atual is TRUE THEN
        RAISE EXCEPTION 'Participação já confirmada';
    END IF;


    UPDATE  participou
    SET confirmado = TRUE
    WHERE id = in_participou_id;

    INSERT INTO log (rotulo, dados)
    VALUES (
      'confirmar_participacao',                  -- Mesmo nome do procedimento
      jsonb_build_object(
        'executado_por',  in_executado_por,
        'participou_id',  in_participou_id,
        'participante_id',  v_participante,
        'encontro_id',  v_encontro
      )
    );
END;
$$;
