SET search_path TO plataforma;

-- Descrição do procedure

CREATE OR REPLACE PROCEDURE cancelar_encontro(
  IN in_executado_por INT,  -- Todos os procedimentos devem receber este no primeiro parâmetro
  IN in_encontro_id   INT
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_valido_atual    BOOLEAN;

BEGIN
    -- Buscar o ID do grupo a partir do encontro
    SELECT o.grupo INTO v_grupo_id
    FROM encontro e
    JOIN ocorreu o ON o.id = e.ocorrencia
    WHERE e.id = in_encontro_id;

    -- Verificar permissão de coordenação para este grupo
    PERFORM plataforma.verificar_permissao(in_executado_por, 'coordenação', v_grupo_id);
    
    SELECT
        valido
        INTO v_valido_atual
        FROM encontro
        WHERE id = in_encontro_id;

  IF v_valido_atual is NULL THEN
      RAISE EXCEPTION 'Não foi encontrado';
    END IF;

  IF v_valido_atual is FALSE THEN
      RAISE EXCEPTION 'Já está cancelado';
    END IF;



  UPDATE encontro
  SET valido = FALSE
  WHERE id = in_encontro_id;

  INSERT INTO log (rotulo, dados)
  VALUES (
    'cancelar_encontro',                  -- Mesmo nome do procedimento
    jsonb_build_object(
      'executado_por', in_executado_por,
      'encontro_id', in_encontro_id
    )
  );
END;
$$;
