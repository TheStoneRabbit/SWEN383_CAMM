package camm.spring.mypls.repositories;

import camm.spring.mypls.domain.Book;
import org.springframework.data.repository.CrudRepository;

public interface BookRepository extends CrudRepository<Book, Long> {

    

}
